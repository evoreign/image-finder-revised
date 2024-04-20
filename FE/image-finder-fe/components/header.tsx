
import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Separator } from './ui/separator';
import { UserButton } from '@clerk/nextjs';
import logo from "../public/logo-dark.png";

const Header: React.FC = () => {
  return (
    <header className="w-full p-2 sm:p-4 fixed top-0 left-0 flex justify-between items-center px-2 sm:px-4 py-1 sm:py-2 bg-transparent z-50 text-black">
      <div className="flex items-center">
        <Link href="/">
            <Image src={logo} alt="Logo" width={100} height={100} className="sm:w-125 sm:h-125" />
        </Link>
      </div>
      <div className="flex h-5 items-center space-x-2 sm:space-x-4 text-xs sm:text-sm">
        <Link href="/" className="text-black hover:text-blue-500">
            Search
        </Link>
        <Separator orientation='vertical'/>
        <Link href="/models" className="text-black hover:text-blue-500">
            Library
        </Link>
        <UserButton/>
      </div>
    </header>
  );
};

export default Header;