from core.writer import Writer

class FileWriter(Writer):
    
    def write(self, distribution, mem_systems):
        outFileHandler = open(self.args.out, 'w')
        
        for i in range(len(mem_systems)):
            outFileHandler.write("# Memory configuration for {0} with size {1} bytes\n".format(mem_systems[i].name, mem_systems[i].realsize))

            for mo in distribution[i]:
                outFileHandler.write("{0} @ {1}\n".format(mo.comment()+mo.callstack, mem_systems[i].allocator))

        outFileHandler.close()
