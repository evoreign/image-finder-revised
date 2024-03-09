import { CollectionConfig } from "payload/types";
export const AttachmentImages: CollectionConfig = {
    slug: "attachment-images",
    admin: {
        useAsTitle: "ModelName",
        description: "Collection for various vehicle model data.",
    },
    fields: [
        {
            name: "ImageID",
            type: "number",
            required: true,
        },
        {
            name:"HashValue",
            type:"text",
            required: false,
        },
        {
            name:"ImageUrl",
            type:"text",
            required: false,
        },
        {
            name: "width",
            type: "number",
            required: true,
        },
        {
            name: "height",
            type: "number",
            required: true,
        }
    ],
}
export default AttachmentImages;