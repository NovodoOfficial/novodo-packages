const fs = require('fs');

let input = '';
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
    try {
        const json = JSON.parse(input);
        
        json.sections.forEach(section => {
            if (section.name === "Github") {
                section.options.forEach(option => {
                    if (option.name === "Github token") {
                        option.value = '';
                    }
                });
            }
        });
        
        process.stdout.write(JSON.stringify(json, null, 2));
    } catch (err) {
        process.stderr.write('Error processing JSON: ' + err.message + '\n');
        process.stdout.write('');
    }
});
