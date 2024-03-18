"use client"
import { useState, useEffect } from 'react';
import { Payment, columns } from "./columns"
import { DataTable } from "./data-table"
import Header from "@/components/header";

interface ApiResponse {
  _id: string;
  Brand: string;
  ModelName: string;
  ImageUrl: string;
  PsType: Record<string, Record<string, { Tab: string, Section: string }>>;
}

async function getData(): Promise<Payment[]> {
  const response = await fetch('http://localhost:4000/search/all');

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const { results } = await response.json();
  return results.map((item: ApiResponse) => ({
    id: item._id,
    brand: item.Brand,
    imgUrl: item.ImageUrl,
    name: item.ModelName,
  }));
}

export default function DemoPage() {
  const [data, setData] = useState<Payment[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const result = await getData();
      setData(result);
    };

    fetchData();
  }, []);

  return (
    <main className="flex flex-col items-center justify-center min-h-screen py-20">
      <Header />
      <h1 className="text-3xl font-bold">Welcome to Image Finder</h1>
      <div className="container mx-auto py-10">
        <DataTable columns={columns} data={data} />
      </div>
    </main>
  )
}