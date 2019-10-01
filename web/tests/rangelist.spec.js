import RangeList from '../src/utils/rangelist';

describe('RangeList', () => {
  it('Specifies first and last member of a subrange', () => {
    const rl = new RangeList();

    rl.add(1);
    rl.add(5, 10);
    let i10 = rl.includes(10);
    expect(i10.member).toBe(true);
    expect(i10.last).toBe(true);

    rl.add(11);
    i10 = rl.includes(10);
    expect(i10.first).toBe(false);
    expect(i10.last).toBe(false);

    const i5 = rl.includes(5);
    expect(i5.first).toBe(true);
    expect(i5.last).toBe(false);

    const i20 = rl.includes(20);
    expect(i20.member).toBe(false);
    expect(i20.first).toBe(false);
  });

  it('Produces non-overlapping ranges', () => {
    const rl = new RangeList();
    rl.add(1);
    expect(rl.members).toContain(1);
    const includes1 = rl.includes(1);
    const includes2 = rl.includes(2);
    expect(includes1.member).toBe(true);
    expect(includes2.member).toBe(false);

    rl.add(5, 3);
    expect(rl.members).not.toContain(2);
    expect(rl.members).toContain(3);
    expect(rl.members).toContain(4);
    expect(rl.members).toContain(5);
    expect(rl.members).not.toContain(6);

    rl.add(3, 4);
    expect(rl.members.length).toBe(4);
  });
});
