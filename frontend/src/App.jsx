import { Routes, Route, Navigate, useLocation, Outlet } from 'react-router-dom';
import { MainLayout } from './components/Layout/MainLayout';
import Dashboard from './Pages/Dashboard';
import AgreementsPage from './Pages/Agreements';
import CreateAgreement from './Pages/CreateAgreement';
import PreviewAgreement from './Pages/PreviewAgreement';
import EditAgreementPage from './Pages/EditAgreement';
import SignIn from './Pages/SignIn';
import ResetPassword from './Pages/ResetPassword';
import ChangePassword from './Pages/ChangePassword';
import React, { useEffect, useState } from 'react';
import ForgotPasswordReset from './Pages/ForgotPasswordReset';
import axiosInstance from './axiosConfig';
 
function isLoggedIn() {
  return (localStorage.getItem('isLoggedIn') && !!localStorage.getItem('token'));
}

// Component to check if user is executive and prevent access to restricted routes
function ProtectedAgreementRoute({ children, restrictedForExecutives = false }) {
  const [isExecutive, setIsExecutive] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkUserPermissions = async () => {
      try {
        // Try to access form-data endpoint - executives will get 403
        await axiosInstance.get('agreements/form-data/');
        // If successful, user is not executive
        setIsExecutive(false);
      } catch (error) {
        // If 403, user is likely executive
        if (error.response?.status === 403) {
          setIsExecutive(true);
        } else {
          // For other errors, assume non-executive to be safe
          setIsExecutive(false);
        }
      } finally {
        setLoading(false);
      }
    };
    checkUserPermissions();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (restrictedForExecutives && isExecutive) {
    return (
      <div style={{ 
        textAlign: 'center', 
        padding: '2rem', 
        color: 'red',
        maxWidth: '600px',
        margin: '2rem auto'
      }}>
        <h2>Access Denied</h2>
        <p>Executive users cannot access this page. You can only view existing agreements.</p>
        <button 
          onClick={() => window.history.back()} 
          style={{ 
            padding: '0.5rem 1rem', 
            background: '#007bff', 
            color: '#fff', 
            border: 'none', 
            borderRadius: '5px', 
            cursor: 'pointer',
            marginTop: '1rem'
          }}
        >
          Go Back
        </button>
      </div>
    );
  }

  return children;
}
 
function ProtectedRoute({ children }) {
  const location = useLocation();
  if (!isLoggedIn()) {
    return <Navigate to="/signin" state={{ from: location }} replace />;
  }
  return children;
}
 
function App() {
  
  return (
    <Routes>
      <Route path="/signin" element={<SignIn />} />
      <Route path="/reset-password" element={<ResetPassword />} />
 
      {/* Public route for forgot password reset */}
      <Route path="/forgot-password-reset" element={<ForgotPasswordReset />} />
 
      {/* Protected routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Outlet />
            </MainLayout>
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="agreements" element={<AgreementsPage />} />
        <Route path="agreements/create" element={
          <ProtectedAgreementRoute restrictedForExecutives={true}>
            <CreateAgreement />
          </ProtectedAgreementRoute>
        } />
        <Route path="agreements/preview/:id" element={<PreviewAgreement />} />
        <Route path="agreements/preview" element={<PreviewAgreement />} />
        <Route path="agreements/edit/:id" element={
          <ProtectedAgreementRoute restrictedForExecutives={true}>
            <EditAgreementPage />
          </ProtectedAgreementRoute>
        } />
        <Route path="change-password" element={<ChangePassword />} />
      </Route>
    </Routes>
  );
}
 
export default App;