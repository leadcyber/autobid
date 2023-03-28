import clipboard from "node-clipboardy";

export const getClipboard = async () => {
    const rt = await clipboard.readSync()
    console.log(rt)
    return rt;
}