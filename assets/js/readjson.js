const fs = require('fs');
const readline = require('readline');

function readJsonFile(filename) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  rl.question(
    "Choose output format (compact/verbose/metadata only): ",
    (answer) => {
      const format = answer.trim().toLowerCase();

      if (!['compact', 'verbose', 'metadata only'].includes(format)) {
        console.error("Invalid choice. Please select 'compact', 'verbose', or 'metadata only'.");
        rl.close();
        return;
      }

      fs.readFile(filename, 'utf8', (err, data) => {
        if (err) {
          console.error(`Error reading file: ${err}`);
          rl.close();
          return;
        }

        try {
          const jsonData = JSON.parse(data);
          let output;
          if (format === 'compact') {
            output = filterData(jsonData, true);
          } else if (format === 'verbose') {
            output = filterData(jsonData, false);
          } else if (format === 'metadata only') {
            output = filterMetadata(jsonData);
            console.log("\nFiltered JSON Contents:", JSON.stringify(output, null, 2));
            const summary = summarizeRemovedData(jsonData, output);
            console.log(generateSummaryText(summary, false));
            rl.close();
            return;
          }

          console.log("\nFiltered JSON Contents:", JSON.stringify(output, null, 2));

          if (format !== 'metadata only') {
            const summary = summarizeRemovedData(jsonData, output);
            console.log(generateSummaryText(summary, format === 'compact'));
          }
        } catch (parseErr) {
          console.error(`Error parsing JSON: ${parseErr}`);
        }

        rl.close();
      });
    }
  );
}

function filterData(data, isCompact) {
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
          filteredData[key] = value
            .filter(item => !isRedundantItem(item))
            .map(item => processChallengeItem(item, key === 'completedChallenges' ? 'completed' : 'saved', isCompact));
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

function filterMetadata(data) {
  const metadataKeys = [
    'about',
    'completedExams',
    'githubProfile',
    'isApisMicroservicesCert',
    'isBackEndCert',
    'isCheater',
    'isDonating',
    'is2018DataVisCert',
    'isDataVisCert',
    'isFrontEndCert',
    'isFullStackCert',
    'isFrontEndLibsCert',
    'isHonest',
    'isInfosecQaCert',
    'isQaCertV7',
    'isInfosecCertV7',
    'isJsAlgoDataStructCert',
    'isRelationalDatabaseCertV8',
    'isRespWebDesignCert',
    'isSciCompPyCertV7',
    'isDataAnalysisPyCertV7',
    'isMachineLearningPyCertV7',
    'isCollegeAlgebraPyCertV8',
    'isFoundationalCSharpCertV8',
    'isJsAlgoDataStructCertV8',
    'linkedin',
    'location',
    'name',
    'partiallyCompletedChallenges',
    'points',
    'portfolio',
    'profileUI',
    'twitter',
    'username',
    'website',
    'yearsTopContributor',
    'currentChallengeId',
    'email',
    'emailVerified',
    'id',
    'sendQuincyEmail',
    'theme',
    'keyboardShortcuts',
    'completedChallengeCount',
    'acceptedPrivacyTerms',
    'isEmailVerified',
    'picture',
    'joinDate',
    'completedSurveys',
    'sessionUser'
  ];
  const metadata = {};

  for (const key of metadataKeys) {
    if (key in data) {
      metadata[key] = data[key];
    }
  }
  return metadata;
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

function removeIdFromItem(item) {
  if (item && typeof item === 'object' && 'id' in item) {
    return { ...item, id: '(id removed)' };
  }
  return item;
}

function processChallengeItem(item, challengeType, isCompact) {
  let processedItem = { ...item };
  processedItem = removeIdFromItem(processedItem);
  if (processedItem.challengeFiles) {
    processedItem.challengeFiles = processedItem.challengeFiles.map(file => 
      replaceContents(file, challengeType, isCompact)
    );
  }
  if (challengeType === 'saved') {
    delete processedItem.history;
  }
  return processedItem;
}

function replaceContents(file, challengeType, isCompact) {
  if (isCompact && file.contents) {
    switch (file.ext) {
      case 'html':
        file.contents = '<!-- HTML content from the assignment -->';
        break;
      case 'css':
        file.contents = '/* CSS content from the assignment */';
        break;
      case 'js':
        file.contents = '/* Javascript content from the assignment */';
        break;
      case 'py':
        file.contents = '# Python content from the assignment';
        break;
      default:
        file.contents = '/* Content from the assignment */';
    }
  }
  return file;
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

  // Process completed challenges
  if (originalData.completedChallenges) {
    originalData.completedChallenges.forEach(challenge => {
      if (isRedundantItem(challenge)) {
        if (challenge.hasOwnProperty('challengeType')) {
          summary.typedExercisesRemoved[challenge.challengeType] = 
            (summary.typedExercisesRemoved[challenge.challengeType] || 0) + 1;
        } else {
          summary.shortExercisesRemoved++;
        }
      }
    });
    originalData.completedChallenges.forEach(countRemovedCode);
  }

  // Process saved challenges
  if (originalData.savedChallenges) {
    originalData.savedChallenges.forEach(countRemovedCode);
  }

  return summary;
}

function generateSummaryText(summary, isCompact) {
  const replacementNote = isCompact
    ? "The original file also contained submitted code, which has been removed and replaced with comments."
    : "The original file also contained submitted code, which has been kept intact.";

  const pythonOccurrencesNote = `Python code is inserted twice in the original database, so this represents ${summary.pythonCodeRemoved / 2} unique occurrences as long as the same structure of the original database files is used.`;

  return `---
The text above is original data from a freeCodeCamp file dump of a .JSON database.

This is an automatically added comment by a parsing app written in JavaScript by Markus Isaksson. The parser has taken a .JSON database file of a freeCodeCamp profile and removed some data. This is a summary of what has been removed:

${summary.shortExercisesRemoved} instances of references to completed shorter step-by-step programming exercises were removed.

${replacementNote}

${summary.htmlCodeRemoved} instances of HTML code were processed.
${summary.cssCodeRemoved} instances of CSS code were processed.
${summary.jsCodeRemoved} instances of JavaScript code were processed.
${summary.pythonCodeRemoved} instances of Python code were processed. ${pythonOccurrencesNote}
${summary.otherCodeRemoved} instances of other types of code were processed.`;
}

const filename = process.argv[2] || 'sample.json';
readJsonFile(filename);
