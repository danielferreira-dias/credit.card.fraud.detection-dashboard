import { useState } from "react";

interface RegisterProps {
  email: string;
  name: string;
  password: string;
  confirm_password: string;
}

interface RegisterRequest {
  email: string;
  name: string;
  password: string;
  confirm_password: string;
}

interface ApiError {
  detail: string | Array<{ loc: string[], msg: string, type: string }>;
}

async function RegisterUser(userData: RegisterProps): Promise<void> {
  // Frontend validation first
  if (userData.password !== userData.confirm_password) {
    throw new Error('Passwords do not match');
  }

  if (userData.password.length < 8) {
    throw new Error('Password must be at least 8 characters long');
  }

  const registerData: RegisterRequest = {
    email: userData.email,
    name: userData.name,
    password: userData.password,
    confirm_password: userData.confirm_password
  };

  try {
    console.log('Sending registration data:', registerData);
    console.log('JSON payload:', JSON.stringify(registerData));
    const response = await fetch('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(registerData)
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();

      // Handle FastAPI validation errors
      if (Array.isArray(errorData.detail)) {
        const errorMessages = errorData.detail.map(err => err.msg).join(', ');
        throw new Error(`Validation error: ${errorMessages}`);
      } else {
        throw new Error(errorData.detail || 'Registration failed');
      }
    }

    const data = await response.json();
    console.log('Registration successful:', data);

    // Store the token from the response structure
    // Backend returns: { user: UserResponse, token: TokenResponse }
    if (data.token && data.token.access_token) {
      localStorage.setItem('access_token', data.token.access_token);
    }

    return data;

  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
}

export default function Register() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<{ [key: string]: string }>({});
  const [touched, setTouched] = useState<{ [key: string]: boolean }>({});

  const validateField = (name: string, value: string) => {
  const errors: { [key: string]: string } = {};

  switch (name) {
      case 'name':
        if (!value.trim()) errors.name = 'Full name is required';
        else if (value.trim().length < 2) errors.name = 'Name must be at least 2 characters';
        break;
      case 'email':
        if (!value.trim()) errors.email = 'Email is required';
        else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) errors.email = 'Please enter a valid email';
        break;
      case 'password':
        if (!value) errors.password = 'Password is required';
        else if (value.length < 8) errors.password = 'Password must be at least 8 characters';
        break;
      case 'confirm_password':
        if (!value) errors.confirm_password = 'Please confirm your password';
        else if (value !== formData.password) errors.confirm_password = 'Passwords do not match';
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
    const allErrors: { [key: string]: string } = {};
    Object.entries(formData).forEach(([key, value]) => {
      const fieldError = validateField(key, value);
      Object.assign(allErrors, fieldError);
    });

    // Mark all fields as touched
    setTouched({
      name: true,
      email: true,
      password: true,
      confirm_password: true
    });

    setFieldErrors(allErrors);

    // Don't submit if there are validation errors
    if (Object.keys(allErrors).length > 0) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await RegisterUser({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        confirm_password: formData.confirm_password
      });
      // ToDo: Add success handling here
      // Registration successful - could redirect or show success message
      window.location.href = "/";
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full h-full flex justify-center items-center p-8 flex-col gap-y-10">
      <form
        onSubmit={handleSubmit}
        className="w-full h-fit min-h-[80%] max-w-md space-y-4 flex flex-col">
        <div>
          <label
            htmlFor="name"
            className="block text-sm font-medium opacity-80 mb-2">
            Full Name
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            onBlur={handleBlur}
            className={`w-full px-4 py-3 bg-[#1A1A1D] border rounded-lg focus:ring-2 text-white placeholder-zinc-400 ${fieldErrors.name
                ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
                : 'border-zinc-600 focus:ring-purple-500 focus:border-transparent'
              }`}
            placeholder="Enter your full name"
            required
          />
          {fieldErrors.name && (
            <p className="text-red-400 text-xs mt-1">{fieldErrors.name}</p>
          )}
        </div>

        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium opacity-80 mb-2">
            Email Address
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            onBlur={handleBlur}
            className={`w-full px-4 py-3 bg-[#1A1A1D] border rounded-lg focus:ring-2 text-white placeholder-zinc-400 ${fieldErrors.email
                ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
                : 'border-zinc-600 focus:ring-purple-500 focus:border-transparent'
              }`}
            placeholder="Enter your email"
            required
          />
          {fieldErrors.email && (
            <p className="text-red-400 text-xs mt-1">{fieldErrors.email}</p>
          )}
        </div>

        <div>
          <label
            htmlFor="password"
            className="block text-sm font-medium opacity-80 mb-2">
            Password
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleInputChange}
            onBlur={handleBlur}
            className={`w-full px-4 py-3 bg-[#1A1A1D] border rounded-lg focus:ring-2 text-white placeholder-zinc-400 ${fieldErrors.password
                ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
                : 'border-zinc-600 focus:ring-purple-500 focus:border-transparent'
              }`}
            placeholder="Enter your password"
            required
          />
          {fieldErrors.password && (
            <p className="text-red-400 text-xs mt-1">{fieldErrors.password}</p>
          )}
        </div>

        <div>
          <label
            htmlFor="confirm_password"
            className="block text-sm font-medium opacity-80 mb-2">
            Confirm Password
          </label>
          <input
            type="password"
            id="confirm_password"
            name="confirm_password"
            value={formData.confirm_password}
            onChange={handleInputChange}
            onBlur={handleBlur}
            className={`w-full px-4 py-3 bg-[#1A1A1D] border rounded-lg focus:ring-2 text-white placeholder-zinc-400 ${fieldErrors.confirm_password
                ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
                : 'border-zinc-600 focus:ring-purple-500 focus:border-transparent'
              }`}
            placeholder="Confirm your password"
            required
          />
          {fieldErrors.confirm_password && (
            <p className="text-red-400 text-xs mt-1">{fieldErrors.confirm_password}</p>
          )}
        </div>

        {error && (
          <div className="text-red-400 text-sm text-center">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-[50%] bg-amber-100 text-black font-medium m-auto py-3 mt-6 px-4 rounded-lg transition duration-200 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-[#0F0F11] disabled:opacity-50 disabled:cursor-not-allowed">
          {isLoading ? 'Creating Account...' : 'Create Account'}
        </button>
      </form>
      <div className="flex flex-row gap-x-10">
        <button>Google</button>
        <button>Github</button>
      </div>
    </div>
  );
}
