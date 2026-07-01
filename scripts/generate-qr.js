const { Client, LocalAuth } = require('whatsapp-web.js');
const client = new Client({
    authStrategy: new LocalAuth({ clientId: 'qr-temp', dataPath: '/tmp/wa-session' }),
    puppeteer: { headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] }
});
client.on('code', code => {
    require('fs').writeFileSync('/tmp/wa-pairing-code.txt', code);
    console.log('CODE=' + code);
});
client.on('ready', () => process.exit(0));
client.initialize().then(() => {
    setTimeout(() => client.requestPairingCode('261387313415').then(c => {
        require('fs').writeFileSync('/tmp/wa-pairing-code.txt', c);
        console.log('CODE=' + c);
    }).catch(e => console.log('ERR='+e.message)), 10000);
}).catch(e => console.log('FAIL='+e.message));
setTimeout(() => process.exit(0), 35000);
