const fs = require('fs');
const zlib = require('zlib');

// Minimal PNG encoder for a solid color icon
function createSolidPng(size, r, g, b) {
    const width = size;
    const height = size;
    
    // PNG signature
    const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
    
    // IHDR chunk
    const ihdr = Buffer.alloc(13);
    ihdr.writeUInt32BE(width, 0);
    ihdr.writeUInt32BE(height, 4);
    ihdr[8] = 8;  // bit depth
    ihdr[9] = 2;  // color type (RGB)
    ihdr[10] = 0; // compression
    ihdr[11] = 0; // filter
    ihdr[12] = 0; // interlace
    
    function crc32(data) {
        let crc = 0xffffffff;
        const table = [];
        for (let n = 0; n < 256; n++) {
            let c = n;
            for (let k = 0; k < 8; k++) {
                c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
            }
            table[n] = c;
        }
        for (let i = 0; i < data.length; i++) {
            crc = table[(crc ^ data[i]) & 0xff] ^ (crc >>> 8);
        }
        return (crc ^ 0xffffffff) >>> 0;
    }
    
    function makeChunk(type, data) {
        const len = Buffer.alloc(4);
        len.writeUInt32BE(data.length);
        const typeData = Buffer.concat([Buffer.from(type), data]);
        const crcV = crc32(typeData);
        const crc = Buffer.alloc(4);
        crc.writeUInt32BE(crcV);
        return Buffer.concat([len, typeData, crc]);
    }
    
    // IDAT - raw image data with filter bytes
    const rawData = [];
    for (let y = 0; y < height; y++) {
        rawData.push(0); // filter byte (none)
        for (let x = 0; x < width; x++) {
            rawData.push(r, g, b);
        }
    }
    
    const compressed = zlib.deflateSync(Buffer.from(rawData));
    
    const ihdrChunk = makeChunk('IHDR', ihdr);
    const idatChunk = makeChunk('IDAT', compressed);
    const iendChunk = makeChunk('IEND', Buffer.alloc(0));
    
    return Buffer.concat([signature, ihdrChunk, idatChunk, iendChunk]);
}

// Create icon with cyan color (#00d9ff)
fs.writeFileSync('app-icon.png', createSolidPng(512, 0x00, 0xd9, 0xff));
console.log('Created app-icon.png (512x512)');

fs.writeFileSync('src-tauri/icons/32x32.png', createSolidPng(32, 0x00, 0xd9, 0xff));
fs.writeFileSync('src-tauri/icons/128x128.png', createSolidPng(128, 0x00, 0xd9, 0xff));
fs.writeFileSync('src-tauri/icons/128x128@2x.png', createSolidPng(256, 0x00, 0xd9, 0xff));
fs.writeFileSync('src-tauri/icons/256x256.png', createSolidPng(256, 0x00, 0xd9, 0xff));
console.log('Updated icons in src-tauri/icons/');
