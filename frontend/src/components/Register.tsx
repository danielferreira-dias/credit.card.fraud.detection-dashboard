import { useState } from "react";
import { GoogleLogin } from "@react-oauth/google";

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
        <div className="bg-white rounded-xl shadow-2xl p-8 w-full max-w-md">
          <h1 className="text-4xl font-bold text-gray-800 text-center mb-8">Sign up</h1>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition duration-200"
                required
              />
            </div>

            <div className="space-y-4">
              <div className="flex items-start space-x-3 justify-center">
                <input
                  id="marketing"
                  type="checkbox"
                  checked={agreedToMarketing}
                  onChange={(e) => setAgreedToMarketing(e.target.checked)}
                  className="mt-1 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                />
                <label htmlFor="marketing" className="text-sm text-gray-600">
                  Auth0 may contact me with marketing communications opt-out details in{" "}
                  <a href="#" className="text-blue-500 underline">Privacy Policy</a>
                </label>
              </div>

              <p className="text-sm text-gray-600">
                By continuing, you agree to the{" "}
                <a href="#" className="text-blue-500 underline">Self Service PSS</a> and{" "}
                <a href="#" className="text-blue-500 underline">Privacy Policy</a>.
              </p>
            </div>

            {error && (
              <div className="text-red-500 text-sm text-center">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 text-white font-medium py-3 px-4 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Creating Account...' : 'Continue'}
            </button>

            <div className="text-center">
              <span className="text-gray-500 text-sm">OR</span>
            </div>

            <div className="space-y-3 flex justify-center">
              <div className="w-full m-auto flex justify-center">
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

            </div>
          </form>
        </div>
      </div>
  );
}
