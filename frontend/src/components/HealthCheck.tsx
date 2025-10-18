"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

export default function HealthCheck() {
  const [status, setStatus] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  const checkHealth = async () => {
    setIsLoading(true);
    setStatus("");
    
    try {
      const response = await fetch("http://localhost:8000/health");
      const data = await response.json();
      setStatus(`✅ Backend is healthy! Status: ${data.status}, Message: ${data.message}`);
    } catch (error) {
      setStatus(`❌ Backend connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">TechMeAnything - Health Check</h1>
      <Button 
        onClick={checkHealth} 
        disabled={isLoading}
        className="mb-4"
      >
        {isLoading ? "Checking..." : "Check Backend Health"}
      </Button>
      
      {status && (
        <div className={`p-4 rounded-md ${
          status.includes("✅") ? "bg-green-50 text-green-800" : "bg-red-50 text-red-800"
        }`}>
          {status}
        </div>
      )}
    </div>
  );
}
