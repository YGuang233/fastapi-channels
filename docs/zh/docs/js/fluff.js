
// update the announcement banner to change the app type
(function() {
  const el = document.getElementById('logfire-app-type');
  const appTypes = [
    ['/news/update/', 'How do I update my project?'], 
    ['/news/update/', 'How to use?'],
    ['/news/update/', 'Updated what?'], 
    
  ];
  const docsUrl = 'https://logfire.pydantic.dev/docs';
  let counter = 0;

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  // avoid multiple replaceText running at the same time (e.g. when the user has left the page)
  let running = false;

  const replaceText = async () => {
    if (running) {
      return;
    }
    running = true;
    try {
      const text = el.textContent;
      for (let i = text.length; i >= 0; i--) {
        el.textContent = text.slice(0, i);
        await sleep(30);
      }
      await sleep(30);
      counter++;
      // change the link halfway through the animation
      const [link, newText] = appTypes[counter % appTypes.length];
      el.href = docsUrl + link;
      await sleep(30);
      for (let i = 0; i <= newText.length; i++) {
        el.textContent = newText.slice(0, i);
        await sleep(30);
      }
    } finally {
      running = false;
    }
  };
  setInterval(replaceText, 4000);
})();
