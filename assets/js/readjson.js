const fs = require('fs');

function readJsonFile(filename) {
  fs.readFile(filename, 'utf8', (err, data) => {
    if (err) {
      console.error(`Error reading file: ${err}`);
      return;
    }

    try {
      const jsonData = JSON.parse(data);
      const filteredData = filterData(jsonData);
      console.log("\nFiltered JSON Contents:", JSON.stringify(filteredData, null, 2));
      const summary = summarizeRemovedData(jsonData, filteredData);
      console.log(generateSummaryText(summary));
    } catch (parseErr) {
      console.error(`Error parsing JSON: ${parseErr}`);
    }
  });
}

function filterData(data) {
  const filteredData = {};
  for (const [key, value] of Object.entries(data)) {
    if (key === 'userToken') {
      filteredData[key] = '(userToken removed)';
    } else if (key === 'id') {
      filteredData[key] = '(id removed)';
    } else if (key === 'website' || key === 'email' || key === 'picture') {
      filteredData[key] = '(Details removed, see LinkedIn profile for contact info)';
    } else if (typeof value === 'object' && value !== null) {
      if (Array.isArray(value)) {
        if (key === 'completedChallenges' || key === 'savedChallenges') {
          filteredData[key] = value.filter(item => !isRedundantItem(item)).map(item => processChallengeItem(item, key === 'completedChallenges' ? 'completed' : 'saved'));
        } else {
          filteredData[key] = value.filter(item => !isRedundantItem(item)).map(item => removeIdFromItem(item));
        }
      } else {
        const filteredObj = filterObject(value);
        if (Object.keys(filteredObj).length > 0) {
          filteredData[key] = removeIdFromItem(filteredObj);
        }
      }
    } else if (!isRedundantEntry(key, value)) {
      filteredData[key] = value;
    }
  }
  return filteredData;
}

function removeIdFromItem(item) {
  if (item && typeof item === 'object' && 'id' in item) {
    return { ...item, id: '(id removed)' };
  }
  return item;
}

function processChallengeItem(item, challengeType) {
  let processedItem = { ...item };
  processedItem = removeIdFromItem(processedItem);
  if (processedItem.challengeFiles) {
    processedItem.challengeFiles = processedItem.challengeFiles.map(file => replaceContents(file, challengeType));
  }
  if (challengeType === 'saved') {
    delete processedItem.history;
  }
  return processedItem;
}

function replaceContents(file, challengeType) {
  const newFile = { ...file };
  const keyField = challengeType === 'completed' ? 'key' : 'fileKey';
  if (newFile.contents) {
    switch (newFile.ext) {
      case 'html':
        newFile.contents = '<!-- HTML content from the assignment -->';
        break;
      case 'css':
        newFile.contents = '/* CSS content from the assignment */';
        break;
      case 'js':
        newFile.contents = '/* Javascript content from the assignment */';
        break;
      case 'py':
        newFile.contents = '# Python content from the assignment';
        break;
      default:
        newFile.contents = '/* Content from the assignment */';
    }
  }
  return newFile;
}

function filterObject(obj) {
  const filteredObj = {};
  for (const [key, value] of Object.entries(obj)) {
    if (!isRedundantEntry(key, value)) {
      filteredObj[key] = value;
    }
  }
  return filteredObj;
}

function isRedundantEntry(key, value) {
  return /^\d{10}$/.test(key) && value === 1;
}

function isRedundantItem(item) {
  if (item.solution) {
    return false;
  }
  return (
    item.completedDate &&
    item.id &&
    item.challengeFiles &&
    item.challengeFiles.length === 0 &&
    (
      (Object.keys(item).length === 3) ||
      (Object.keys(item).length === 4 && item.hasOwnProperty('challengeType'))
    )
  );
}

function summarizeRemovedData(originalData, filteredData) {
  const summary = {
    shortExercisesRemoved: 0,
    typedExercisesRemoved: {},
    htmlCodeRemoved: 0,
    cssCodeRemoved: 0,
    jsCodeRemoved: 0,
    pythonCodeRemoved: 0,
    otherCodeRemoved: 0
  };
  originalData.completedChallenges.forEach(challenge => {
    if (isRedundantItem(challenge)) {
      if (challenge.hasOwnProperty('challengeType')) {
        summary.typedExercisesRemoved[challenge.challengeType] = (summary.typedExercisesRemoved[challenge.challengeType] || 0) + 1;
      } else {
        summary.shortExercisesRemoved++;
      }
    }
  });
  const countRemovedCode = (challenge) => {
    challenge.challengeFiles?.forEach(file => {
      if (file.contents) {
        switch (file.ext) {
          case 'html':
            summary.htmlCodeRemoved++;
            break;
          case 'css':
            summary.cssCodeRemoved++;
            break;
          case 'js':
            summary.jsCodeRemoved++;
            break;
          case 'py':
            summary.pythonCodeRemoved++;
            break;
          default:
            summary.otherCodeRemoved++;
        }
      }
    });
  };
  originalData.completedChallenges.forEach(countRemovedCode);
  originalData.savedChallenges?.forEach(countRemovedCode);
  return summary;
}

function generateSummaryText(summary) {
  let typedExercisesText = Object.entries(summary.typedExercisesRemoved)
    .map(([type, count]) => `${count} instances of references to completed programming exercises that had a (type ${type}) were removed`)
    .join('\n');

  return ` ---
The above text was original data from a freeCodeCamp file dump of a .JSON database.

This is an automatically added comment by a parsing app written in JavaScript by Markus Isaksson. The parser has taken a .JSON database file of a freeCodeCamp profile and removed some data. This is summary of what has been removed:

${summary.shortExercisesRemoved} instances of references to completed shorter step by step programming exercises without type number were removed

${typedExercisesText}

The original file also contained submitted HTML, CSS, JavaScript, and Python code which has been removed and replaced with comments. Such code is viewable through the links on the person's official digital certificates.

${summary.htmlCodeRemoved} of HTML code pieces were removed
${summary.cssCodeRemoved} of CSS code pieces were removed
${summary.jsCodeRemoved} of JavaScript code pieces were removed
${summary.pythonCodeRemoved} of Python code pieces were removed
${summary.otherCodeRemoved} of other code pieces were removed`;
}

const filename = process.argv[2] || 'sample.json';
readJsonFile(filename);