import ffmpeg

inputfile = r"C:\Users\sequel2\AppData\Roaming\Fanvil\recorded\2018-08-27.bak\out_3001_2011_0c383e213ff2_2018-08-27_12_24_20.g722"
outputfile = r"C:\Users\sequel2\AppData\Roaming\Fanvil\recorded\2018-08-27.bak\out_3001_2011_0c383e213ff2_2018-08-27_12_24_20_converted.wav"

stream = ffmpeg.input(inputfile, f='g722', ac=1)
stream = ffmpeg.output(stream, outputfile, ar='8k', ac=1, acodec='pcm_s16le')
print(str(stream))
ffmpeg.run(stream)

