import { CollectionConfig } from "payload/types";
export const AttachmentImagesSift: CollectionConfig = {
    slug: "attachment-images-sift",
    admin: {
        useAsTitle: "ImageID",
        description: "Collection for various attachment images.",
    },
    upload: true,
    fields: [
        {
            name: "ImageID",
            type: "number",
            required: false,
        },
        {
            name:"Embeddings",
            type:"text",
            required: false,
        }
    ],
}
export default AttachmentImagesSift;