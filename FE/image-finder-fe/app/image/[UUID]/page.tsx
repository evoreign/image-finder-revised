'use client';
import { useEffect, useState } from 'react';
import Header from "@/components/header";
import axios from 'axios'; // Import Axios

import { useSearchParams } from 'next/navigation'

type ParamsType = {
    UUID: string; // Corrected to string as it's typically a UUID
};


export default function ImagePage({ params }: { params: ParamsType }) {
    const [imageData, setImageData] = useState<ImageData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const searchParams = useSearchParams();
    const fileName = searchParams.get('fileName');

    useEffect(() => {
        const fetchImageData = async () => {
            try {
                const response = await axios.get<ImageData>(`http://127.0.0.1:80/imagesearch/${params.UUID}`);
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
                    <h1>Image for {fileName}</h1>
                    <pre>{JSON.stringify(imageData, null, 2)}</pre>
                </div>
            )}
        </main>
    );
}