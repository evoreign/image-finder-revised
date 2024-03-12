import Header from "@/components/header";
import { SignIn, SignUp } from "@clerk/nextjs";
export default function SignUpPage() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen py-20">
      <Header />
      <SignUp />
    </main>
  );
}