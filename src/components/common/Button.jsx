import React from 'react';
import { Loader2 } from 'lucide-react';

export default function Button({
  children,
  variant = 'primary', // primary | secondary | accent | outline | danger | ghost
  size = 'md',        // sm | md | lg
  icon: Icon = null,
  loading = false,
  disabled = false,
  className = '',
  onClick,
  type = 'button',
  ...props
}) {
  const sizeClass = size === 'sm' ? 'btn-sm' : size === 'lg' ? 'btn-lg' : '';

  return (
    <button
      type={type}
      disabled={disabled || loading}
      aria-busy={loading}
      onClick={onClick}
      className={`btn btn-${variant} ${sizeClass} ${className}`}
      {...props}
    >
      {loading ? (
        <Loader2 size={size === 'sm' ? 14 : 18} style={{ animation: 'spin 1s linear infinite' }} />
      ) : Icon ? (
        <Icon size={size === 'sm' ? 14 : 18} />
      ) : null}
      <span>{children}</span>
    </button>
  );
}
