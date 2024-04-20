import React, { useState } from 'react';
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { MagnifyingGlassIcon } from '@radix-ui/react-icons'; // Import Radix UI Icons
import { Label } from "@/components/ui/label"
import Link from 'next/link';

const SearchBar: React.FC = () => {
  const [image, setImage] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setImage(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (image) {
      const formData = new FormData();
      formData.append('image', image);

      try {
        const response = await fetch('127.0.0.1:6000/search', {
          method: 'POST',
          body: formData,
        });
        // Handle response
      } catch (error) {
        // Handle error
      }
    }
  };

  return (
    <div className="flex w-full max-w-sm items-center space-x-2">
      <div className="grid w-full max-w-sm items-center gap-1.5">
        <Label htmlFor="picture">Enter picture you want to search</Label>
        <Input id="picture" type="file" accept="image/png, image/jpeg" onChange={handleFileChange} />
      </div>
      <Button onClick={handleUpload}>
        <MagnifyingGlassIcon className="text-gray text-4xl" />
      </Button>
    </div>
  );
};

export default SearchBar;
