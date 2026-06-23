import React from 'react';
import { describe, expect, it } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App.jsx';

describe('Power BI embedded demo app', () => {
  it('checks the backend Microsoft master-token session before showing the custom login page', async () => {
    render(<App />);

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith('/api/auth/microsoft/status', { credentials: 'include' });
    });
    expect(await screen.findByRole('heading', { name: /carpro embedded analytics demo/i })).toBeInTheDocument();
  });

  it('starts on the warehouse-backed login page', async () => {
    render(<App />);

    expect(await screen.findByRole('heading', { name: /carpro embedded analytics demo/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/user mail/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /login as executive/i })).not.toBeInTheDocument();
  });

  it('loads warehouse users from the backend without changing the login page design', async () => {
    const user = userEvent.setup();
    render(<App />);

    const ag001 = await screen.findByRole('button', { name: /ag001@mail.com/i });
    await user.click(ag001);

    expect(screen.getByLabelText(/user mail/i)).toHaveValue('AG001@mail.com');
  });

  it('logs in with warehouse credentials, switches dashboards, changes password, and logs out', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(await screen.findByLabelText(/user mail/i), 'EXECUTIVE@mail.com');
    await user.type(screen.getByLabelText(/password/i), 'EXECUTIVE');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1, name: /sales & quotation dashboard/i })).toBeInTheDocument();
    expect(screen.getByText(/executive@mail.com - admin/i)).toBeInTheDocument();

    const navigation = screen.getByRole('navigation', { name: /dashboard navigation/i });
    await user.click(within(navigation).getByRole('button', { name: /policy & payment operation/i }));
    expect(screen.getByRole('heading', { level: 1, name: /policy & payment operation dashboard/i })).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /change password/i }));
    expect(screen.getByRole('dialog', { name: /change password/i })).toBeInTheDocument();
    await user.type(screen.getByLabelText(/current password/i), 'EXECUTIVE');
    await user.type(screen.getByLabelText(/^new password$/i), 'newpass');
    await user.type(screen.getByLabelText(/confirm password/i), 'newpass');
    await user.click(screen.getByRole('button', { name: /update password/i }));
    expect(await screen.findByText(/password updated/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /logout/i }));
    expect(screen.getByRole('heading', { name: /carpro embedded analytics demo/i })).toBeInTheDocument();
  });
});
