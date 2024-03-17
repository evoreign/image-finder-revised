"use client"
import { useState, useEffect } from 'react';
import { Payment, columns } from "./columns"
import { DataTable } from "./data-table"
import Header from "@/components/header";

// async function getData(): Promise<Payment[]> {
//   const response = await fetch('http://localhost:4000/api/models');
//   if (!response.ok) {
//       throw new Error(`HTTP error! status: ${response.status}`);
//   }
//   const data = await response.json();
//   return data;
// }
async function getData(): Promise<Payment[]> {
  // Fetch data from your API here.
  return [
    {
      id: "728ed52f",
      brand: "KOM",
      imgUrl: "https://res.cloudinary.com/dxatvm6sr/image/upload/v1710070137/attachment-images/wa04halkakzte6f25x1x.png",
      name: "m@example.com",
    },
    {
      id: "728ed52f",
      brand: "LIE",
      imgUrl: "https://res.cloudinary.com/dxatvm6sr/image/upload/v1710070137/attachment-images/wa04halkakzte6f25x1x.png",
      name: "test",
    },
    {
      id: "728ed52f",
      brand: "LIE",
      imgUrl: "https://res.cloudinary.com/dxatvm6sr/image/upload/v1710070137/attachment-images/wa04halkakzte6f25x1x.png",
      name: "test1",
    },

    // ...
  ]
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