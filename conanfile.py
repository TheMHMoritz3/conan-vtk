from conans import ConanFile, CMake, tools
from shutil import copyfile
import os


class LibnameConan(ConanFile):
    name = "libvtk"
    description = "Keep it short"
    topics = ("conan", "libname", "logging")
    url = "https://github.com/bincrafters/conan-libname"
    homepage = "https://github.com/original_author/original_lib"
    license = "MIT"  # Indicates license type of the packaged library; please use SPDX Identifiers https://spdx.org/licenses/
    # Remove following lines if the target lib does not use CMake
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    version = "7.1.1"
    # Options may need to change depending on the packaged library
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "Examples": [True, False], "Rendering": [True, False]}
    default_options = {"shared": True, "fPIC": True, "Examples": False, "Rendering": True}
    _extractionfolder = "source_subfolder"
    _source_subfolder = "source_subfolder/VTK-7.1.1"
    _build_subfolder = "build_subfolder"

    requires = (
        "zlib/1.2.11",
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.download("https://www.vtk.org/files/release/7.1/VTK-7.1.1.zip", "vtk.zip")
        tools.unzip("vtk.zip", self._extractionfolder)
        tools.replace_in_file(self._source_subfolder + "/CMakeLists.txt", "project(VTK)",
                               '''project(VTK)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = True

        cmake.definitions["BUILD_EXAMPLES"] = self.options.Examples
        cmake.definitions["BUILD_TESTINGS"] = False
        cmake.definitions["BUILD_SHARED"] = True

        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return cmake

    def build(self):
        if not os.path.exists(self._build_subfolder):
            os.makedirs(self._build_subfolder)
        copyfile("./conanbuildinfo.cmake", self._build_subfolder + "/conanbuildinfo.cmake")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can just remove the lines below
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
