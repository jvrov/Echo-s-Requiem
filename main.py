import pygame
import math
import random

# Constantes
LARGURA = 1200
ALTURA = 700
FPS = 60

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
AZUL_ETEREO = (100, 150, 255)
ROXO_SOMBRIO = (75, 0, 130)

class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill((100, 100, 100))  # Cinza para plataformas
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        pass  # Plataformas estáticas não precisam de update

class Echo(pygame.sprite.Sprite):
    def __init__(self, grupos):
        super().__init__(grupos)
        # Atributos visuais
        self.image = pygame.Surface((50, 70))
        self.image.fill(AZUL_ETEREO)
        self.rect = self.image.get_rect()
        self.rect.center = (LARGURA // 2, ALTURA // 2)
        
        # Atributos de movimento
        self.velocidade_x = 0
        self.velocidade_y = 0
        self.velocidade_base = 8
        self.gravidade = 0.8
        self.forca_pulo = -16
        self.no_chao = False
        
        # Atributos de combate
        self.vida = 100
        self.vida_maxima = 100
        self.energia = 100
        self.energia_maxima = 100
        self.atacando = False
        self.invulneravel = False
        self.timer_invulneravel = 0
        
        # Atributos de dash
        self.dash_disponivel = True
        self.dash_velocidade = 15
        self.dash_duracao = 10
        self.dash_timer = 0
        self.dash_cooldown = 30
        
        # Fragmentos coletados
        self.fragmentos = 0
        self.total_fragmentos = 5

    def pular(self):
        if self.no_chao:
            self.velocidade_y = self.forca_pulo
            self.no_chao = False

    def dash(self):
        if self.dash_disponivel and self.energia >= 20:
            self.dash_disponivel = False
            self.dash_timer = self.dash_duracao
            self.energia -= 20
            # Criar efeito de partículas
            self.criar_particulas_dash()

    def atacar(self):
        if not self.atacando and self.energia >= 10:
            self.atacando = True
            self.energia -= 10
            # Criar hitbox do ataque
            self.criar_hitbox_ataque()

    def update(self, teclas, plataformas):
        # Movimento horizontal
        self.velocidade_x = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.velocidade_x = -self.velocidade_base
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.velocidade_x = self.velocidade_base

        # Pulo
        if (teclas[pygame.K_SPACE] or teclas[pygame.K_w]) and self.no_chao:
            self.pular()

        # Dash
        if teclas[pygame.K_LSHIFT] and self.dash_disponivel:
            self.dash()

        # Ataque
        if teclas[pygame.K_x]:
            self.atacar()

        # Aplicar gravidade
        if not self.no_chao:
            self.velocidade_y += self.gravidade
            
        # Atualizar posição
        self.rect.x += self.velocidade_x
        self.rect.y += self.velocidade_y

        # Colisão com plataformas
        self.checar_colisoes(plataformas)

        # Regenerar energia
        if self.energia < self.energia_maxima:
            self.energia += 0.2

        # Atualizar timers
        if self.dash_timer > 0:
            self.dash_timer -= 1
        elif not self.dash_disponivel:
            self.dash_disponivel = True

    def checar_colisoes(self, plataformas):
        # Colisão com plataformas
        self.no_chao = False
        
        # Verificar cada plataforma
        for plataforma in plataformas:
            if self.rect.colliderect(plataforma.rect):
                # Colisão por baixo da plataforma
                if self.velocidade_y < 0:
                    self.rect.top = plataforma.rect.bottom
                    self.velocidade_y = 0
                # Colisão por cima da plataforma
                elif self.velocidade_y > 0:
                    self.rect.bottom = plataforma.rect.top
                    self.velocidade_y = 0
                    self.no_chao = True
                # Colisão lateral
                else:
                    if self.velocidade_x > 0:
                        self.rect.right = plataforma.rect.left
                    elif self.velocidade_x < 0:
                        self.rect.left = plataforma.rect.right

    def criar_particulas_dash(self):
        # Efeito visual do dash (será implementado depois)
        pass

    def criar_hitbox_ataque(self):
        # Criar hitbox do ataque (será implementado depois)
        direcao = 1 if self.velocidade_x >= 0 else -1
        hitbox_x = self.rect.right if direcao > 0 else self.rect.left - 50
        hitbox = pygame.Rect(hitbox_x, self.rect.y, 50, self.rect.height)
        # Verificar colisões com inimigos usando esta hitbox

class Jogo:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Echo's Requiem")
        self.clock = pygame.time.Clock()
        self.rodando = True

        # Criar grupos
        self.todos_sprites = pygame.sprite.Group()
        self.plataformas = pygame.sprite.Group()
        self.inimigos = pygame.sprite.Group()
        self.projeteis = pygame.sprite.Group()

        # Criar jogador
        self.echo = Echo([self.todos_sprites])
        
        # Criar plataformas iniciais
        self.criar_plataformas()

    def criar_plataformas(self):
        # Plataforma base (chão)
        plataforma = Plataforma(0, ALTURA - 40, LARGURA, 40)
        self.plataformas.add(plataforma)
        self.todos_sprites.add(plataforma)

        # Algumas plataformas flutuantes
        plataformas_lista = [
            (300, ALTURA - 200, 200, 20),
            (600, ALTURA - 350, 200, 20),
            (100, ALTURA - 350, 200, 20),
            (800, ALTURA - 200, 200, 20)
        ]

        for x, y, w, h in plataformas_lista:
            plataforma = Plataforma(x, y, w, h)
            self.plataformas.add(plataforma)
            self.todos_sprites.add(plataforma)

    def rodar(self):
        while self.rodando:
            self.clock.tick(FPS)
            
            # Eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False

            # Input
            teclas = pygame.key.get_pressed()

            # Update
            self.echo.update(teclas, self.plataformas)
            self.inimigos.update()
            self.projeteis.update()

            # Draw
            self.tela.fill(PRETO)
            self.todos_sprites.draw(self.tela)
            
            # HUD
            self.desenhar_hud()
            
            pygame.display.flip()

        pygame.quit()

    def desenhar_hud(self):
        # Barra de vida
        pygame.draw.rect(self.tela, (255, 0, 0), (20, 20, self.echo.vida, 20))
        # Barra de energia
        pygame.draw.rect(self.tela, (0, 0, 255), (20, 50, self.echo.energia, 20))
        # Fragmentos coletados
        texto = f"Fragmentos: {self.echo.fragmentos}/{self.echo.total_fragmentos}"
        # Renderizar texto aqui...

if __name__ == '__main__':
    jogo = Jogo()
    jogo.rodar()