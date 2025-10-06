import { useState } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";

async function RegisterUser(email: string): Promise<void> {
  const registerData = { email };

  try {
    const response = await fetch('http://localhost:80/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(registerData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Registration failed');
    }

    const data = await response.json();

    if (data.token && data.token.access_token) {
      localStorage.setItem('access_token', data.token.access_token);
    }
    window.location.href = "/";
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
}

export default function Register() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agreedToMarketing, setAgreedToMarketing] = useState(false);

  const validateEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.trim()) {
      setError('Email is required');
      return;
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await RegisterUser(email);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse: any) => {
    console.log('Google login success:', credentialResponse);

    if (!credentialResponse.credential) {
      setError('No credential received from Google');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Send Google token to your backend for verification and user registration/login
      const response = await fetch('http://localhost:80/auth/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: credentialResponse.credential
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Google authentication failed');
      }

      const data = await response.json();

      // Store the backend-issued access token
      if (data.token && data.token.access_token) {
        localStorage.setItem('access_token', data.token.access_token);
        window.location.href = "/";
      } else {
        throw new Error('No access token received from server');
      }
    } catch (error) {
      console.error('Google authentication error:', error);
      setError(error instanceof Error ? error.message : 'Google authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleFailure = () => {
    console.log('Google login failed');
    setError('Google login failed. Please try again.');
  };

  return (
    <div className="min-h-screen h-full bg-[#161719] flex w-full items-center justify-center p-4">
      <div className="flex flex-col gap-6 w-full max-w-md">
        <Card>
          <CardHeader>
            <CardTitle>Create an account</CardTitle>
            <CardDescription>
              Enter your email below to create your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit}>
              <FieldGroup>
                <Field>
                  <FieldLabel htmlFor="email">Email</FieldLabel>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="m@example.com"
                    required
                  />
                </Field>

                <Field>
                  <div className="flex items-start space-x-3">
                    <input
                      id="marketing"
                      type="checkbox"
                      checked={agreedToMarketing}
                      onChange={(e) => setAgreedToMarketing(e.target.checked)}
                      className="mt-1 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                    />
                    <FieldDescription className="text-left">
                      Auth0 may contact me with marketing communications opt-out details in{" "}
                      <a href="#" className="text-primary underline underline-offset-4 hover:no-underline">Privacy Policy</a>
                    </FieldDescription>
                  </div>
                </Field>

                <Field>
                  <FieldDescription className="text-center">
                    By continuing, you agree to the{" "}
                    <a href="#" className="text-primary underline underline-offset-4 hover:no-underline">Self Service PSS</a> and{" "}
                    <a href="#" className="text-primary underline underline-offset-4 hover:no-underline">Privacy Policy</a>.
                  </FieldDescription>
                </Field>

                {error && (
                  <Field>
                    <FieldDescription className="text-destructive text-center">
                      {error}
                    </FieldDescription>
                  </Field>
                )}

                <Field>
                  <Button type="submit" disabled={isLoading}>
                    {isLoading ? 'Creating Account...' : 'Continue'}
                  </Button>
                  <FieldDescription className="text-center">
                    <span className="text-muted-foreground text-sm">OR</span>
                  </FieldDescription>
                  <div className="w-full flex justify-center">
                    <GoogleLogin
                      onSuccess={handleGoogleSuccess}
                      onError={handleGoogleFailure}
                      auto_select={true}
                      theme="outline"
                      text="continue_with"
                      shape="rectangular"
                      width="100%"
                    />
                  </div>
                  <FieldDescription className="text-center">
                    Already have an account? <a href="#" className="text-primary underline underline-offset-4 hover:no-underline">Sign in</a>
                  </FieldDescription>
                </Field>
              </FieldGroup>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
