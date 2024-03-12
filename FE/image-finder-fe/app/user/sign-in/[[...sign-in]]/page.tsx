import Header from "@/components/header";
import { SignIn } from "@clerk/nextjs";
export default function SignInPage() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen py-20">
      <Header />
      <SignIn />
    </main>
  );
}