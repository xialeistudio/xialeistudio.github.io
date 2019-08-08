function replace<T extends {new(...args: any[]):{}}>(target: T) {
    return class extends target {
        newname = "newName";
        age = 18
    }
}

@replace
class Demo {
    oldname = "oldname";
    constructor(oldname: string) {
        this.oldname = oldname;
    }
}

console.log(new Demo("oldname"));
