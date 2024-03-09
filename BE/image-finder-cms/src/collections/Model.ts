import { CollectionConfig } from "payload/types";
export const Models: CollectionConfig = {
    slug: "models",
    auth: true,
    fields: [
        {
            name: "ModelName",
            type: "text",
            required: true,
        },
        {
            name: "PsType",
            type: "number",
            required: true,
        },
        {
            name:"ImageUrl",
            type:"text",
            required: false,
        },
        {
            name: "Data",
            type: "json",
            required: true,
        }
    ],
}