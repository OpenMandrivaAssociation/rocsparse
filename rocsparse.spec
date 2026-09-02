# HIP sparse linear algebra (TheRock 10.0)

Name:		rocsparse
Version:	10.0.0
Release:	1
Summary:	HIP sparse linear algebra library
License:	MIT
Group:		System/Libraries
URL:		https://github.com/ROCm/rocm-libraries
Source0:	https://github.com/ROCm/rocm-libraries/releases/download/therock-10.0/rocsparse.tar.gz#/rocsparse-%{version}.tar.gz
# Clang 23 freestanding headers no longer pull in strncpy/memcpy via transitive includes
Patch0:		0001-include-cstring.patch

BuildRequires:	rocm-rpm-macros
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	rocm-cmake
BuildRequires:	hipcc
BuildRequires:	rocminfo
BuildRequires:	clang-tools
BuildRequires:	rocm-hip-devel
BuildRequires:	clang >= %{rocm_llvm_maj_ver}
BuildRequires:	rocprim-devel
# Optional deps disabled until packaged
# BuildRequires:	rocblas-devel
# BuildRequires:	roctracer / roctx


%description
rocSPARSE implements sparse BLAS and related operations for HIP.
Built for GPU targets including gfx803. Optional rocBLAS and rocTX
integration is disabled until those packages exist.

%package devel
Summary:	Development files for rocsparse
Group:		Development/C++
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	rocm-hip-devel
Requires:	rocprim-devel
Provides:	rocsparse-devel = %{EVRD}

%description devel
Headers and CMake package for rocsparse.

%prep
%autosetup -n rocsparse -p1

export CXX=hipcc
export CC=clang
export ROCM_PATH=%{_prefix}
export HIP_PATH=%{_prefix}
CXXFLAGS=$(printf '%s' "%{optflags}" | sed -E 's/-mfpmath=[^ ]+//g; s/ -m[a-z0-9+.=]+//g')
export CXXFLAGS
export CFLAGS="$CXXFLAGS"
export LDFLAGS=$(printf '%s' "%{?__global_ldflags}" | sed -E 's/-mfpmath=[^ ]+//g; s/ -m[a-z0-9+.=]+//g')
%cmake %{rocm_cmake_fhs} %{rocm_cmake_gpu_targets_prim} \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_CXX_COMPILER=hipcc \
	-DCMAKE_CXX_FLAGS="$CXXFLAGS" \
	-DBUILD_CLIENTS_TESTS=OFF \
	-DBUILD_CLIENTS_BENCHMARKS=OFF \
	-DBUILD_CLIENTS_SAMPLES=OFF \
	-DBUILD_SHARED_LIBS=ON \
	-DBUILD_WITH_ROCBLAS=OFF \
	-DBUILD_WITH_ROCTX=OFF \
	-DBUILD_DOCS=OFF \
	-DROCM_PATH=%{_prefix} \
	-DCMAKE_PREFIX_PATH=%{_prefix} \
	-G Ninja

%build
%ninja_build -C build

%install
%ninja_install -C build
if [ -d %{buildroot}/usr/lib/cmake/rocsparse ] && [ ! -d %{buildroot}%{_libdir}/cmake/rocsparse ]; then
	mkdir -p %{buildroot}%{_libdir}/cmake
	mv %{buildroot}/usr/lib/cmake/rocsparse %{buildroot}%{_libdir}/cmake/
	rmdir %{buildroot}/usr/lib/cmake 2>/dev/null || true
	rmdir %{buildroot}/usr/lib 2>/dev/null || true
fi

%files
%license LICENSE.md
%doc README.md
%exclude %{_docdir}/rocsparse/LICENSE.md
%{_libdir}/librocsparse.so.*

%files devel
%{_includedir}/rocsparse/
%{_libdir}/librocsparse.so
%{_libdir}/cmake/rocsparse/
