import { useState } from "react";

export default function Login() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Login form submitted:", formData);
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
            className="w-full px-4 py-3 bg-[#1A1A1D] border border-zinc-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white placeholder-zinc-400"
            placeholder="Enter your email"
            required
          />
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
            className="w-full px-4 py-3 bg-[#1A1A1D] border mb-6 border-zinc-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white placeholder-zinc-400"
            placeholder="Enter your password"
            required
          />
        </div>

        <button
          type="submit"
          className="w-[50%] bg-amber-100 text-black font-medium m-auto py-3 mt-6 px-4 rounded-lg transition duration-200 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-[#0F0F11]">
          Sign In
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
