import React, { useState } from 'react';
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { MagnifyingGlassIcon } from '@radix-ui/react-icons';
import { Label } from "@/components/ui/label"
import axios from 'axios'; // Import Axios
import { useRouter } from 'next/navigation'; // Import useRouter instead of next/navigation

const SearchBar: React.FC = () => {
  const [image, setImage] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const router = useRouter(); // Initialize useRouter

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setImage(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (image) {
      setLoading(true);
      setError(null);
      setSuccess(false);
      const formData = new FormData();
      formData.append('image', image);

      try {
        const response = await axios.post('http://127.0.0.1:80/search', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        });
        console.log('Response:', response.data);
        // Handle response
        setLoading(false);
        setSuccess(true);
        // Redirect user to the new URL with UUID and filename as query parameters
        router.push(`/image/${response.data.UUID}?fileName=${encodeURIComponent(image.name)}`);
      } catch (error) {
        // Handle error
        console.error('Error uploading image:', error);
        setLoading(false);
        setError('An error occurred. Please try again.');
      }
    }
  };

  return (
    <div className="flex w-full max-w-sm items-center space-x-2">
      <div className="grid w-full max-w-sm items-center gap-1.5">
        <Label htmlFor="picture">Enter picture you want to search</Label>
        <Input id="picture" type="file" accept="image/png, image/jpeg" onChange={handleFileChange} />
      </div>
      <Button onClick={handleUpload} disabled={loading}>
        {loading ? (
          <div>Loading...</div>
        ) : (
          <MagnifyingGlassIcon className="text-gray text-4xl" />
        )}
      </Button>
      {error && <div className="text-red-500">{error}</div>}
      {success && <div className="text-green-500">Upload successful!</div>}
    </div>
  );
};

export default SearchBar;
