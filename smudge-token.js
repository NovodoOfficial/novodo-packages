const fs = require('fs');

const configFilePath = './config.json';
let configData;

try {
  configData = JSON.parse(fs.readFileSync(configFilePath, 'utf8'));
} catch (err) {
  console.error('Error reading the config file:', err);
  process.exit(1);
}

configData.sections.forEach(section => {
  section.options.forEach(option => {
    if (option.hasOwnProperty('default')) {
      option.value = option.default;
    }
  });
});

try {
  fs.writeFileSync(configFilePath, JSON.stringify(configData, null, 4));
  console.log('Config reset to default values successfully.');
} catch (err) {
  console.error('Error writing to the config file:', err);
  process.exit(1);
}
