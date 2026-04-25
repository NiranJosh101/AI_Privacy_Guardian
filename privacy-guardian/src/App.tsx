import { useState } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
// 1. Change BrowserRouter to HashRouter
import { HashRouter, Routes, Route, Navigate } from "react-router-dom";
import { UserConfiguration } from "@/types/privacy";
import Onboarding from "./pages/Onboarding";
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => {
  const [config, setConfig] = useState<UserConfiguration | null>(null);

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        {/* 2. Use HashRouter here */}
        <HashRouter>
          <Routes>
            <Route path="/" element={config ? <Navigate to="/dashboard" /> : <Onboarding onComplete={setConfig} />} />
            <Route path="/dashboard" element={<Dashboard config={config} />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </HashRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;