export default {
  //Shuffle a given Array
  shuffleArray(array) {
    return array.sort(() => Math.random() - 0.5);
  },

  addArrayToItselfNTimes(originalArray, n) {
    let resultArray = [];

    for (let i = 0; i < n; i++) {
      resultArray = resultArray.concat(originalArray);
    }

    return this.shuffleArray(resultArray);
  },

  //Tile Icon Generation for login background
  ensureMinimumLength(allImages) {
    const MIN_LENGTH = 24;
    const flatImages = allImages.flat();

    if (flatImages.length < MIN_LENGTH) {
      const requiredLength = Math.ceil((MIN_LENGTH - flatImages.length) / flatImages.length + 1);
      const duplicatedArray = this.addArrayToItselfNTimes(flatImages, requiredLength);
      return duplicatedArray.slice(0, MIN_LENGTH);
    } else if (flatImages.length > MIN_LENGTH) {
      return flatImages.slice(0, MIN_LENGTH);
    }

    return flatImages;
  }

}