interface FormInputProps {
  id: string;
  name: string;
  type: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur: (e: React.FocusEvent<HTMLInputElement>) => void;
  placeholder: string;
  label: string;
  error?: string;
  required?: boolean;
}

export default function FormInput({ id, name, type,value,onChange,onBlur,placeholder,label,error,required = false }: FormInputProps) {
  return (
<div className="mt-6">
  <label htmlFor={id} className="block text-sm font-medium opacity-80 mb-2"> {label}
  </label>
  <input type={type} id={id} name={name} value={value} onChange={onChange} onBlur={onBlur} className={`w-full px-4 py-3 bg-[#1A1A1D] border rounded-lg focus:ring-2 text-white placeholder-zinc-400 ${ error? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-zinc-600 focus:ring-purple-500 focus:border-transparent'}`}
  placeholder={placeholder} required={required}/>
  {error && (
    <p className="text-red-400 text-xs mt-1">{error}</p>
  )}
</div>
  );
}