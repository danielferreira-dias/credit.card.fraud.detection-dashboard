import { useState } from "react";

async function LoginUser(email: string, password: string): Promise<void> {
  const loginData = { email, password };

  try {
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }

    const data = await response.json();
    console.log('Login successful:', data);

    // Store the token securely (consider using HttpOnly cookies for better security)
    localStorage.setItem('access_token', data.access_token);

    // Redirect or update UI as needed
  } catch (error) {
    console.error('Login error:', error);
    throw error; // Let the calling component handle the error display
  }
}

export default function Login() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<{[key: string]: string}>({});
  const [touched, setTouched] = useState<{[key: string]: boolean}>({});

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
      // ToDo: Add success handling here
      // Login successful - could redirect or show success message
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
        className="w-full h-[60%] max-w-md space-y-4 flex flex-col">
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
            className={`w-full px-4 py-3 bg-[#1A1A1D] border rounded-lg focus:ring-2 text-white placeholder-zinc-400 ${
              fieldErrors.email
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
            className={`w-full px-4 py-3 bg-[#1A1A1D] border rounded-lg focus:ring-2 text-white placeholder-zinc-400 ${
              fieldErrors.password
                ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
                : 'border-zinc-600 focus:ring-purple-500 focus:border-transparent'
            }`}
            placeholder="Enter your password"
            required
          />
          {fieldErrors.password && (
            <p className="text-red-400 text-xs mt-1 mb-4">{fieldErrors.password}</p>
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
          {isLoading ? 'Signing In...' : 'Sign In'}
        </button>

        <div className="text-center">
          <button
            type="button"
            className="text-sm text-amber-200 hover:text-purple-300 transition duration-200 mt-3">
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
