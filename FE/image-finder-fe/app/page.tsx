"use client";
import Header from "@/components/header";
import { AuroraBackground } from "@/components/ui/aurora-background";
import React from "react";

function Home() {
  
  return (
    <AuroraBackground>
      <main className="flex flex-col items-center justify-center min-h-screen py-20">
        <Header />
        <h1 className="text-3xl font-semibold">Welcome to Image Finder</h1>
      </main>
    </AuroraBackground>
  );
}
export default Home;