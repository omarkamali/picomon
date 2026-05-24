{
  description = "Picomon ~ TUI for monitoring GPUs";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
  inputs.pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";

  outputs =
    { nixpkgs, pyproject-nix, ... }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs lib.systems.flakeExposed;

      project = pyproject-nix.lib.project.loadPyproject {
        projectRoot = ./.;
      };

      pythonAttr = "python313";
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          python = pkgs.${pythonAttr};
        in
        {
          default = python.pkgs.buildPythonPackage (project.renderers.buildPythonPackage { inherit python; });
        }
      );
    };
}
