/**
 * An inefficient rangelist
 * because there shouldn't be a large fragmented list of ranges.
 */
export default class RangeList {
  constructor(initial = []) {
    this.members = initial;
  }

  /**
   * Binary search for el
   * @param {Number} el element to find
   */
  _find(el) {
    let lowIndex = 0;
    let highIndex = this.members.length - 1;
    while (lowIndex <= highIndex) {
      const midIndex = Math.floor((lowIndex + highIndex) / 2);
      if (this.members[midIndex] === el) {
        return midIndex;
      } if (this.members[midIndex] < el) {
        lowIndex = midIndex + 1;
      } else {
        highIndex = midIndex - 1;
      }
    } return null;
  }

  /**
   * Add range to members
   * @param {Number} a first index
   * @param {Number} b optional last index
   */
  add(a, b = null) {
    let nin = a;
    let nout = b !== null ? b : a;
    if (nout < nin) {
      const tmp = nin;
      nin = nout;
      nout = tmp;
    }
    for (let i = nin; i <= nout; i += 1) {
      if (this.members.indexOf(i) === -1) {
        this.members.push(i);
      }
    }
    this.members = this.members.sort((j, k) => j - k);
  }

  /**
   * Check membership of index
   * @param {Number} a
   * @returns Object<{member: Boolean, first: Boolean, last:Boolean}>
   */
  includes(a) {
    const foundIndex = this._find(a);
    if (foundIndex !== null) {
      const first = (foundIndex === 0)
          || (this.members[foundIndex - 1] !== a - 1);
      const last = (foundIndex === this.members.length - 1)
          || (this.members[foundIndex + 1] !== a + 1);
      return { member: true, first, last };
    }
    return { member: false };
  }
}
