import { useState } from "react";
import FormInput from "./FormInput";

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
    const response = await fetch('http://localhost:80/auth/register', {
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

    
    if (data.token && data.token.access_token) {
      localStorage.setItem('access_token', data.token.access_token);
    }
    window.location.href = "/";
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

  const formFields = [
    {
      name: "name",
      type: "text",
      label: "Full Name",
      placeholder: "Enter your full name",
    },
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
    {
      name: "confirm_password",
      type: "password",
      label: "Confirm Password",
      placeholder: "Confirm your password",
    },
  ];

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
        className="w-full max-w-md flex flex-col ">
        {formFields.map((field) => (
          <FormInput key={field.name} id={field.name} name={field.name} type={field.type} value={formData[field.name as keyof typeof formData]} onChange={handleInputChange} onBlur={handleBlur} placeholder={field.placeholder} label={field.label} error={fieldErrors[field.name]} required
          />
        ))}

        {error && (
          <div className="text-red-400 text-sm text-center">
            {error}
          </div>
        )}

        <button type="submit" disabled={isLoading} className="w-[50%] bg-amber-100 text-black font-medium m-auto py-3 mt-6 px-4 rounded-lg transition duration-200 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-o [#0F0F11] disabled:opacity-50 disabled:cursor-not-allowed"> {isLoading ? 'Creating Account...' : 'Create Account'}
        </button>
      </form>
      <div className="flex flex-row gap-x-10">
        <button>Google</button>
        <button>Github</button>
      </div>
    </div>
  );
}
