const express = require('express');
const axios = require("axios");

const app = express();
const PORT = process.env.PORT || 3000;

app.get("/", (req, res) => {
  res.send("<h1>Vardiyalı Bot Sistemi Aktif</h1><p>20'şerli gruplar halinde 3 saatlik vardiyalarla çalışıyor.</p>");
});

app.listen(PORT, () => console.log(`Sunucu ${PORT} portunda aktif.`));

const tokensString = process.env.TOKENS; 
const channelIdsString = process.env.CHANNEL_ID;
const message1 = "BURAYA 1. MESAJI YAZIN"; // Değişken yerine direkt koddan da değiştirebilirsin
const message2 = "BURAYA 2. MESAJI YAZIN";

if (!tokensString || !channelIdsString) {
    console.error("HATA: Değişkenler eksik!");
} else {
    const allTokens = tokensString.split(',').map(t => t.trim());
    const channelIds = channelIdsString.split(',').map(c => c.trim());
    
    // Tokenları 20'şerli iki gruba ayır
    const groupA = allTokens.slice(0, 20);
    const groupB = allTokens.slice(20, 40);

    let currentGroup = "A"; // Başlangıç grubu

    console.log("Sistem başlatıldı. Vardiya süresi: 3 Saat.");

    // Ana Döngü Fonksiyonu
    const runVardiya = () => {
        const activeTokens = currentGroup === "A" ? groupA : groupB;
        const groupLabel = currentGroup === "A" ? "Grup 1 (İlk 20)" : "Grup 2 (Son 20)";
        
        console.log(`🚀 Vardiya Değişimi: Şu an aktif olan: ${groupLabel}`);

        activeTokens.forEach((token, index) => {
            const startBot = () => {
                // 0.5sn temel hız + insan taklidi sapması
                const jitter = Math.floor(Math.random() * 100) - 50; 
                const interval = 500 + jitter;

                setTimeout(async () => {
                    // Sadece doğru vardiyadaysa mesaj at
                    if ((currentGroup === "A" && groupA.includes(token)) || 
                        (currentGroup === "B" && groupB.includes(token))) {
                        
                        await sendRandomMessage(token, channelIds, index + 1);
                        startBot(); // Döngüyü devam ettir
                    }
                }, interval);
            };
            
            // Botları kademeli başlat
            setTimeout(startBot, index * 500);
            // DND Moduna sok
            updateStatus(token);
        });
    };

    // İlk vardiyayı başlat
    runVardiya();

    // 3 Saatte bir vardiya değiştir (3 * 60 * 60 * 1000 ms)
    setInterval(() => {
        currentGroup = currentGroup === "A" ? "B" : "A";
        console.log("🔄 3 saat doldu, vardiya değişiyor...");
        runVardiya();
    }, 3 * 60 * 60 * 1000);
}

async function sendRandomMessage(token, ids, botNo) {
    const messages = [message1, message2];
    const selectedMessage = messages[Math.floor(Math.random() * messages.length)];
    const finalMsg = `${selectedMessage} (${Math.floor(Math.random() * 999)})`;

    for (const id of ids) {
        try {
            axios.post(`https://discord.com/api/v9/channels/${id}/typing`, {}, { headers: { "Authorization": token } }).catch(() => {});
            
            await axios.post(`https://discord.com/api/v9/channels/${id}/messages`, 
                { content: finalMsg }, 
                { headers: { "Authorization": token, "Content-Type": "application/json" } }
            );
            console.log(`✅ Bot #${botNo} mesaj gönderdi.`);
        } catch (err) {
            if (err.response?.status === 429) console.log("⏳ Hız sınırı.");
        }
    }
}

async function updateStatus(token) {
    axios.patch(`https://discord.com/api/v9/users/@me/settings`, { status: "dnd" }, { headers: { "Authorization": token } }).catch(() => {});
}
