'use client';
import { useEffect, useState } from 'react';
import Header from "@/components/header";
import axios from 'axios'; // Import Axios
import Image from 'next/image'

import { useSearchParams } from 'next/navigation'; // Correct import for useSearchParams

type ParamsType = {
    UUID: string; // Corrected to string as it's typically a UUID
};

interface ImageData {
    original_filename: string;
    secure_url: string;
}

export default function ImagePage({ params }: { params: ParamsType }) {
    const [imageData, setImageData] = useState<ImageData[] | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const searchParams = useSearchParams();
    const fileName = searchParams.get('fileName');

    useEffect(() => {
        const fetchImageData = async () => {
            try {
                const response = await axios.get<ImageData[]>(`http://127.0.0.1:80/imagesearch/${params.UUID}`);
                setImageData(response.data);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching image data:', error);
                setLoading(false);
                setError('Your image is in the queue. Please check again later (30 sec - 5 min).');
            }
        };

        fetchImageData();
    }, [params.UUID]);

    return (
        <main className="flex flex-col items-center justify-center min-h-screen py-20">
            <Header />
            {loading && <div>Loading...</div>}
            {error && <div>{error}</div>}
            {imageData && (
                <div>
                    <h1>Images for {fileName}</h1>
                        {imageData.map((image, index) => (
                            <div className='hover:bg-gray-500'key={index}>
                                <Image
                                    src={image.secure_url}
                                    alt={image.original_filename}
                                    width={250}
                                    height={250}
                                    loading='lazy'
                                    quality={80}
  
                                />
                                <p>{image.original_filename}</p>
                            </div>
                        ))}

                </div>
            )}
        </main>
    );
}

