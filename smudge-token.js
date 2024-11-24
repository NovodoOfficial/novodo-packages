const fs = require('fs');

let data = '';

process.stdin.on('data', chunk => {
  data += chunk;
});

process.stdin.on('end', () => {
  try {
    if (!data) {
      console.error('No input received.');
      process.exit(1);
    }

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
    console.error('Error processing the config:', err);
    process.exit(1);
  }
});
