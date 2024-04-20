"use client";
import Header from "@/components/header";
import { AuroraBackground } from "@/components/ui/aurora-background";
import React from "react";
import SearchBar from "@/components/search-bar";
import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"
import Link from 'next/link';
function Home() {
  
  return (

      <main className="flex flex-col items-center justify-center min-h-screen py-20">
        <Header />
        <h1 className="text-3xl font-semibold">Welcome to Image Finder</h1>
        <SearchBar />
      </main>

  );
}
export default Home;