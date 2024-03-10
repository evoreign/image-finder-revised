import Header from "@/components/header";

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen py-20">
      <Header />
      <h1 className="text-3xl font-bold">Welcome to Image Finder</h1>
    </main>
  );
}
