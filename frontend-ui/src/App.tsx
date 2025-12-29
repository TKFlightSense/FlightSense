import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import DepartmentDashboard from "./pages/DepartmentDashboard";
import CreateUser from "./pages/CreateUser";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public route */}
        <Route path="/" element={<Login />} />

        <Route
          path="/admin/create-user"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <CreateUser />
            </ProtectedRoute>
          }
        />


        {/* Manager/Admin dashboard */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute allowedRoles={["admin", "manager"]}>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Department dashboards (viewer + manager/admin can see) */}
        <Route
          path="/department/:departmentName"
          element={
            <ProtectedRoute
              allowedRoles={["viewer", "manager", "admin"]}
            >
              <DepartmentDashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
