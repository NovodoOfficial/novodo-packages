const fs = require('fs');

const configFilePath = '/dev/stdin';

let data = '';
process.stdin.on('data', chunk => {
  data += chunk;
});
process.stdin.on('end', () => {
  try {
    let config = JSON.parse(data);

    config.sections.forEach(section => {
      if (section.name === 'Github') {
        section.options.forEach(option => {
          if (option.name === 'Github token') {
            option.value = '';
          }
        });
      }
    });

    process.stdout.write(JSON.stringify(config, null, 4));
  } catch (err) {
    console.error('Error processing config:', err);
    process.exit(1);
  }
});
