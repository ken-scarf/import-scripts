{
  inputs.nixpkgs.url = github:NixOS/nixpkgs/nixos-unstable;
  outputs = {self, nixpkgs}: 
    let 
      supportedSystems = ["x86_64-linux"];
      forAllSystems = f: nixpkgs.lib.genAttrs supportedSystems (system: f system);
      nixpkgsFor = forAllSystems(system: import nixpkgs {
        inherit system;
        overlays = [self.overlay];
      });
    in { 
      overlay = self: super: {};

      devShells = forAllSystems(system: 
        let 
          pkgs = nixpkgsFor.${system};
        in {
          default = pkgs.mkShell {
            packages = with pkgs; [
              pkgs.python3
              (pkgs.python3.withPackages (python-pkgs: [ 
                python-pkgs.requests
              ]))
            ];
            shellHook = ''
              export PS1='[$PWD]\nscarf-shell ❄ '
            '';
          };
        });
    };
}
