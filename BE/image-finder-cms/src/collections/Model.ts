import { CollectionConfig } from "payload/types";
export const Models: CollectionConfig = {
    slug: "models",
    admin: {
        useAsTitle: "ModelName",
        description: "Collection for various vehicle model data.",
    },
    fields: [
        {
            name: "Brand",
            type: "text",
            required: true,
        },
        {
            name: "ModelName",
            type: "text",
            required: true,
        },
        {
            name:"ImageUrl",
            type:"text",
            required: false,
        },
        {
            name: "PsType",
            type: "json",
            required: true,
        },
    ],
}
export default Models