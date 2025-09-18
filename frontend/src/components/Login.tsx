import { useState } from "react";
import FormInput from "./FormInput";
import { useUser } from "../context/UserContext";

async function LoginUser(email: string, password: string): Promise<void> {
  const loginData = { email, password };

  try {
    const response = await fetch('http://localhost:80/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }

    const data = await response.json();

    // Store the token securely (consider using HttpOnly cookies for better security)
    if (data.token && data.token.access_token) {
      localStorage.setItem('access_token', data.token.access_token);
    }
    window.location.href = "/";
    // Redirect or update UI as needed
  } catch (error) {
    console.error('Login error:', error);
    throw error; // Let the calling component handle the error display
  }
}

export default function Login() {
  const { refreshUser } = useUser();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<{[key: string]: string}>({});
  const [touched, setTouched] = useState<{[key: string]: boolean}>({});

  const formFields = [
    {
      name: "email",
      type: "email",
      label: "Email Address",
      placeholder: "Enter your email",
    },
    {
      name: "password",
      type: "password",
      label: "Password",
      placeholder: "Enter your password",
    },
  ];

  const validateField = (name: string, value: string) => {
    const errors: {[key: string]: string} = {};

    switch (name) {
      case 'email':
        if (!value.trim()) errors.email = 'Email is required';
        else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) errors.email = 'Please enter a valid email';
        break;
      case 'password':
        if (!value) errors.password = 'Password is required';
        break;
    }

    return errors;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });

    // Validate field if it's been touched
    if (touched[name]) {
      const fieldError = validateField(name, value);
      setFieldErrors(prev => {
        const newErrors = { ...prev, ...fieldError };
        if (Object.keys(fieldError).length === 0) {
          delete newErrors[name];
        }
        return newErrors;
      });
    }
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));

    const fieldError = validateField(name, value);
    setFieldErrors(prev => {
      const newErrors = { ...prev, ...fieldError };
      if (Object.keys(fieldError).length === 0) {
        delete newErrors[name];
      }
      return newErrors;
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all fields
    const allErrors: {[key: string]: string} = {};
    Object.entries(formData).forEach(([key, value]) => {
      const fieldError = validateField(key, value);
      Object.assign(allErrors, fieldError);
    });

    // Mark all fields as touched
    setTouched({
      email: true,
      password: true
    });

    setFieldErrors(allErrors);

    // Don't submit if there are validation errors
    if (Object.keys(allErrors).length > 0) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await LoginUser(formData.email, formData.password);
      await refreshUser();
      window.location.href = "/";
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full h-full flex flex-col justify-center items-center p-8 gap-y-10 ">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md  flex flex-col">
        {formFields.map((field) => (
          <FormInput key={field.name} id={field.name} name={field.name} type={field.type} value={formData[field.name as keyof typeof formData]} onChange={handleInputChange} onBlur={handleBlur} placeholder={field.placeholder} label={field.label} error={fieldErrors[field.name]} required />
        ))}

        {error && (
          <div className="text-red-400 text-sm text-center">
            {error}
          </div>
        )}

        <button type="submit" disabled={isLoading} className="w-[50%] bg-amber-100 text-black font-medium m-auto py-3 mt-6 px-4 rounded-lg transition duration-200 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-o [#0F0F11] disabled:opacity-50 disabled:cursor-not-allowed"> {isLoading ? 'Signing In...' : 'Sign In'}
        </button>

        <div className="text-center">
          <button type="button" className="text-sm text-amber-200 hover:text-purple-300 transition duration-200 mt-3">
            Forgot your password?
          </button>
        </div>
      </form>
      <div className="flex flex-row gap-x-10">
        <button>Google</button>
        <button>Github</button>
      </div>
    </div>
  );
}
