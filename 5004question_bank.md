## &#x23;week 2

Question 1:

When a user-level application running in an operating system needs to perform an operation that requires access to hardware, what happens?

Options:

A. The application passes the request to another user-level process

B. The application accesses the hardware directly

C. The application makes a system call to request the kernel to perform the operation ✅

D. The operation is blocked unless the application is in kernel space

E. The operation is queued until the application has higher privileges

Analysis:

The correct answer is C. User-level applications operate in "User Mode" (Ring 3) and cannot access hardware directly for security reasons. They must switch to "Kernel Mode" (Ring 0) via a system call to ask the OS kernel to perform the task.↳

Distractor B: Incorrect because direct hardware access by user apps would bypass OS security protections.

Distractor D: Incorrect because the operation isn't blocked; the mode switches during the system call.

Distractor E: Incorrect because system calls are executed immediately (synchronously or asynchronously), not just queued based on privilege escalation.↳

Question 2:

How does the operating system handle load balancing in a multi-core processor environment?

Options:

A. By allowing processes to migrate freely without restriction

B. By distributing processes and threads across available cores to optimize performance ✅

C. By assigning higher priority to I/O-bound processes

D. By executing all processes sequentially on a single core

E. By pinning all threads to a single core

Analysis:

The correct answer is B. The OS scheduler (e.g., CFS in Linux) attempts to balance the workload (threads/processes) across all available CPU cores to maximize throughput and minimize latency.

Distractor A: Incorrect because migration is controlled by the scheduler to maintain cache affinity, not "freely without restriction."

Distractor D: Incorrect because this negates the benefit of having multiple cores.

Distractor E: Incorrect because pinning all threads to one core (processor affinity) prevents load balancing.↳

Question 3:

In the context of virtual memory, what is a “page”?

Options:

A. A fixed-size block of memory that can be swapped ✅

B. A segment of a process’s code

C. A fixed-size block of data stored in the cache

D. A physical segment of a hard drive

E. A section of the CPU register

Analysis:

The correct answer is A. Virtual memory divides the address space into fixed-size units called "pages" (typically 4KB). These pages map to "page frames" in physical RAM and can be swapped out to disk.↳

Distractor B: Refers to "Segmentation," a different memory management technique.

Distractor C: Refers to a "Cache Line."

Distractor D: Refers to a "Sector" or "Block" on a disk.

Question 4:

You are in the /usr/local/bin directory. What is the correct command to navigate to /usr/local/share/docs using a relative path?

Options:

A. cd /share/docs

B. cd /usr/local/share/docs

C. cd ../share/docs ✅

D. cd ./share/docs

E. cd ../bin/share/docs

Analysis:

The correct answer is C. The .. symbol moves the user up one level (to /usr/local), and then the path descends into share/docs.↳

Distractor B: This is an absolute path, not a relative path.

Distractor D: The ./ represents the current directory, so this looks for share inside bin, which is incorrect.

Distractor A: This attempts to go to the root /share, which likely does not exist or is the wrong location.

Question 5:

If you are in the /var/log directory, which of the following commands will take you to the /etc directory?

Options:

A. cd /etc ✅

B. cd ./etc

C. cd ../etc

D. cd /var/etc

E. cd etc

Analysis:

The correct answer is A. /etc is an absolute path (starting with /). Absolute paths work regardless of the user's current working directory.

Distractor C: Moving up one level (..) from /var/log lands you in /var. There is no standard etc folder inside /var.

Distractor E: Without the leading /, the shell looks for a folder named etc inside the current directory (/var/log), which does not exist.↳

Question 6:

What will the following command do: echo "Hello" > greetings.txt?

Options:

A. Creates a file greetings.txt and writes “Hello” into it, overwriting existing content ✅

B. Prints “Hello” to the terminal

C. Opens greetings.txt for reading

D. Appends “Hello” to the greetings.txt file

E. Creates a new file greetings.txt but leaves it empty

Analysis:

The correct answer is A. The > operator redirects standard output to a file. If the file exists, it is truncated (overwritten); if not, it is created.

Distractor B: This happens only if there is no redirection (>).

Distractor D: Appending requires the >> operator.

Distractor E: This would happen if you used touch or redirected empty output.↳

Question 7:

Which command correctly uses brace expansion to create three empty files: file1.txt, file2.txt, and file3.txt?

Options:

A. touch file(1..3).txt

B. touch file{1..3}.txt ✅

C. touch file{1-3}.txt

D. touch file(1,2,3).txt

E. touch file[1-3].txt

Analysis:

The correct answer is B. Bash brace expansion uses curly braces {..} to generate a sequence. file{1..3}.txt expands to file1.txt file2.txt file3.txt.

Distractor A & D: Parentheses () are used for subshells or arrays, not expansion sequences.

Distractor E: Square brackets [] are used for pattern matching (globbing) of existing files, not for generating new filenames.

Question 8:

If you execute sleep 200 & and then immediately type wait, what is the expected behavior?

Options:

A. The sleep command will be paused

B. The shell will wait for the sleep command to finish ✅

C. The shell will bring the sleep process to the foreground

D. The sleep command will be terminated

E. The sleep command will be restarted

Analysis:

The correct answer is B. The & runs sleep in the background. The wait command instructs the shell to pause execution until all background jobs (child processes) have completed.

Distractor C: To bring a background process to the foreground, you would use fg.

Distractor D: To terminate, you would use kill.

Question 9:

Which process state indicates that the process has completed, but the parent process has not yet read its exit status?

Options:

A. Interruptible Sleep (S)

B. Running (R)

C. Uninterruptible Sleep (D)

D. Stopped (T)

E. Zombie (Z) ✅

Analysis:

The correct answer is E. A "Zombie" process (marked with Z) is a process that has finished execution (died), but its entry remains in the process table because the parent has not yet called wait() to read its exit code.

Distractor A: The process is waiting for an event (like input).

Distractor D: The process has been paused (usually by a signal like SIGSTOP).

Question 10:

To convert all lowercase characters to uppercase in notes.txt, which command should be used?

Options:

A. cat notes.txt | grep '[A-Z]'

B. sort 'A-Z' notes.txt

C. tr 'a-z' 'A-Z' < notes.txt ✅

D. sed 's/[a-z]/[A-Z]/g' notes.txt

E. cut 'a-z' 'A-Z' notes.txt

Analysis:

The correct answer is C. tr (translate) replaces characters in the first set (a-z) with corresponding characters in the second set (A-Z).

Distractor D: While sed can transform text, the syntax s/[a-z]/[A-Z]/g is invalid for changing case in standard sed (it requires special escapes like \U or y///).

Distractor A: grep searches for lines matching a pattern; it does not transform text.

Question 11:

How can you replace all instances of the word “error” with “warning” in a file called logfile.txt?

Options:

A. grep warning logfile.txt | sed 's/error/warning/g'

B. cut 'error' logfile.txt | tr 'warning'

C. sort logfile.txt | sed 's/warning/error/g'

D. tr error warning < logfile.txt

E. sed 's/error/warning/g' logfile.txt ✅

Analysis:

The correct answer is E. sed (stream editor) uses the substitution command s/find/replace/g. The g flag ensures all instances on a line are replaced, not just the first.↳

Distractor D: tr translates individual characters, not whole words. It would map 'e'->'w', 'r'->'a', etc.

Distractor A: This pipes the output of grep (which only finds lines already containing "warning") into sed, which is logically backwards for this task.↳

Question 12:

Which command is used to create a compressed archive of a directory using tar and gzip?

Options:

A. tar -cf archive.tar.gz directory/

B. tar -rf archive.tar.gz directory/

C. tar -czf archive.tar.gz directory/ ✅

D. tar -xzf archive.tar.gz directory/

E. gzip -cz directory/ > archive.tar.gz

Analysis:

The correct answer is C.↳

* -c: Create archive.↳

* -z: Filter through gzip (compression).↳

* -f: Output to filename.↳

Distractor A: Lacks the -z flag, so it would create an uncompressed tarball (despite the .gz extension).

Distractor D: -x is for extracting, not creating.↳

Question 13:

How would you extract a .tar.gz file into the current directory?

Options:

A. tar -xf archive.tar

B. gzip -d archive.tar.gz

C. tar -c archive.tar.gz

D. tar -xzf archive.tar.gz ✅

E. tar -r archive.tar.gz

Analysis:

The correct answer is D.↳

* -x: Extract.↳

* -z: Decompress (gzip).

* -f: Read from file.

Distractor B: gzip -d only decompresses the file, leaving you with archive.tar, but it does not extract the files out of the tarball container.

Distractor C: -c is for create.↳

Question 14:

What command would you use to uninstall a package from a conda environment?

Options:

A. conda deactivate package_name

B. conda remove package_name ✅

C. conda purge package_name

D. conda uninstall package_name

E. conda delete package_name

Analysis:

The correct answer is B. conda remove is the primary command to remove packages. (Note: conda uninstall is an alias for remove and is also technically valid, but remove is the canonical command).↳

Distractor A: deactivate is for exiting the environment, not removing packages.

Distractor C: purge is a command used in apt (Debian/Ubuntu), not Conda.↳

Question 15:

Which of the following commands would you use to install a compiled C/C++ program into system directories (such as /usr/local/bin)?

Options:

A. make

B. make configure

C. make clean

D. ./configure install

E. sudo make install ✅

Analysis:

The correct answer is E. The install target in a Makefile copies the compiled binaries to their destination. Since system directories like /usr/local/bin are write-protected, sudo is required.↳

Distractor A: make only compiles the code; it does not move it to system directories.

Distractor D: ./configure is usually run before make to prepare the build, it does not accept an install argument directly.↳
