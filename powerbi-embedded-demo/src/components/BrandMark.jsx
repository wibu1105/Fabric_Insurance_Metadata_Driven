import React from 'react';
export default function BrandMark({ variant = 'white' }) {
  const logo = variant === 'red' ? '/assets/nashtech-logo-red.png' : '/assets/nashtech-logo-white.png';
  return (
    <div className={`brand-mark brand-mark--${variant}`}>
      <img src={logo} alt="NashTech" />
    </div>
  );
}
