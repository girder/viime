import Vue from 'vue';
/**
 * An inefficient rangelist
 * because there shouldn't be a large fragmented list of ranges.
 */
export default class RangeList {
  constructor(initial = []) {
    this.members_ = {};
    initial.forEach((i) => this.add(i));
  }

  get members() {
    return Object.keys(this.members_)
      .map((m) => parseInt(m, 10))
      .sort((a, b) => a - b);
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
      Vue.set(this.members_, i, true);
    }
  }

  /**
   * Check membership of index
   * @param {Number} a
   * @returns Object<{member: Boolean, first: Boolean, last:Boolean}>
   */
  includes(a) {
    const member = this.members_[a] || false;
    const first = !this.members_[a - 1] && member;
    const last = !this.members_[a + 1] && member;
    return { member, first, last };
  }
}
